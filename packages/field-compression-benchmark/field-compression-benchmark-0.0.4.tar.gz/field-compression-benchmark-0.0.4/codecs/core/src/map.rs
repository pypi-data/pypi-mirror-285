#[allow(clippy::module_name_repetitions)]
pub trait HigherOrderMap {
    type Args<T: crate::ty::BufferTyBound>;
    type Output<T: crate::ty::BufferTyBound>;

    fn map<T: crate::ty::BufferTyBound>(self, args: Self::Args<T>) -> Self::Output<T>;
}

#[macro_export]
#[allow(clippy::module_name_repetitions)]
macro_rules! map_with {
    (
        for < $($lt:lifetime,)* $T:ident $(, $p:ident : $w:path)* $(,)? >
        || -> $ret:ty $block:block
    ) => {
        $crate::map_with!(
            for < $($lt,)* $T $(, $p: $w)* > move() | | -> $ret $block
        )
    };
    (
        for < $($lt:lifetime,)* $T:ident $(, $p:ident : $w:path)* $(,)? >
        move($($v:ident: $t:ty),* $(,)?) || -> $ret:ty $block:block
    ) => {
        $crate::map_with!(
            for < $($lt,)* $T $(, $p: $w)* > move($($v: $t),*) | | -> $ret $block
        )
    };
    (
        for < $($lt:lifetime,)* $T:ident $(, $p:ident : $w:path)* $(,)? >
        | $($a:ident: $at:ty),* $(,)? | -> $ret:ty $block:block
    ) => {
        $crate::map_with!(
            for < $($lt,)* $T $(, $p: $w)* > move() |$($a: $at),*| -> $ret $block
        )
    };
    (
        for < $($lt:lifetime,)* $T:ident $(, $p:ident : $w:path)* $(,)? >
        move($($v:ident: $t:ty),* $(,)?) | $($a:ident: $at:ty),* $(,)? | -> $ret:ty $block:block
    ) => {
        {
            struct HigherOrderClosure<$($lt,)* $($p: $w),*> {
                $($v: $t,)*
                _marker: $crate::core::marker::PhantomData::<($(&$lt (),)* $($p),*)>,
            }

            impl<$($lt,)* $($p: $w),*> $crate::map::HigherOrderMap
                for HigherOrderClosure<$($lt,)* $($p),*>
            {
                #[allow(unused_parens)]
                type Args<$T: $crate::BufferTyBound> = ($($at),*);
                type Output<$T: $crate::BufferTyBound> = $ret;

                fn map<$T: $crate::BufferTyBound>(
                    self, args: Self::Args<$T>
                ) -> Self::Output<$T> {
                    #[allow(unused_parens)]
                    let ($($a),*): ($($at),*) = args;
                    $(let $v: $t = self.$v;)*
                    $block
                }
            }

            HigherOrderClosure {
                $($v,)*
                _marker: $crate::core::marker::PhantomData,
            }
        }
    }
}
